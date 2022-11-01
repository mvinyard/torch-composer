
__module_name__ = "_base_torch_neural_net.py"
__doc__ = """
          The most important module in the package to construct pytorch
          neural nets from an ordered dictionary.
          """
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])
__version__ = "0.0.1"


# -- import packages: --------------------------------------------------------------------
from collections import OrderedDict
import torch


# -- import local dependencies: ----------------------------------------------------------
from ._abstract_base_models import BaseTorchDict, BaseNeuralNet
from ._supporting_functions import parse_kwargs, io_dim, as_list, is_null
from ._layer import Layer


# -- Supporting objects: -----------------------------------------------------------------
class TorchDict(BaseTorchDict):
    def __init__(
        self,
        in_dim,
        out_dim,
        hidden={1: [25, 25], 2: [25, 25]},
        activation_function=torch.nn.LeakyReLU(),
        dropout=0,
        input_bias=True,
        output_bias=True,
    ):
        super(TorchDict, self).__init__()

        self.ignore = ["self", "activation_function", "dropout"]
        self.out = self.__register__(args=locals())

    def __register__(self, args):
        
        # if not is_null(args["hidden"]):
        self.in_n, self.out_m, self.n_hidden = io_dim(args["hidden"])
        self.activation_functions = as_list(
            args["activation_function"], n=int(self.n_hidden+1)
        )
        self.dropouts = as_list(args["dropout"], n=self.n_hidden)
        [args.pop(item) for item in self.ignore]
        self.__dict__.update(args)

    def __compose__(self):
        """returned upon __call__"""
        NNDict = {}

        # -- do input: -------------------------------------------------------------------
        layer_dict = Layer(name=None,
                           nodes_m=self.in_dim,
                           nodes_n=self.in_n,
                           bias=self.input_bias,
                           layer_type="input",
                          )()
        NNDict["input"] = layer_dict["input"]

        # -- do hidden: ------------------------------------------------------------------
        if not is_null(self.hidden):
            for n, (layer, nodes) in enumerate(self.hidden.items()):
                layer_dict = Layer(
                    name=layer,
                    nodes_m=nodes[0],
                    nodes_n=nodes[1],
                    activation_function=self.activation_functions[n],
                    dropout=self.dropouts[n],
                    bias=True,
                    layer_type="hidden",
                )()
                for k, v in layer_dict.items():
                    NNDict[k] = v

        # -- do output: ------------------------------------------------------------------
        # NNDict["output"] 
        layer_dict = Layer(
            name=None,
            nodes_m=self.out_m,
            nodes_n=self.out_dim,
            activation_function=self.activation_functions[-1],
            bias=self.output_bias,
            layer_type="output",
        )()
        for k, v in layer_dict.items():
            if k == "output":
                NNDict[k] = v
            else:
                NNDict["output_{}".format(k)] = v
        return NNDict


# -- Main module class - non-user facing: ------------------------------------------------
class TorchNeuralNet(BaseNeuralNet):
    def __init__(
        self,
        in_dim,
        out_dim,
        hidden={1: [200, 200]},
        activation_function=torch.nn.LeakyReLU(),
        dropout=0,
        input_bias=True,
        output_bias=True,
    ) -> OrderedDict:
        self.args = locals()

    def __define__(self):
        kwargs = parse_kwargs(self.args)
        return TorchDict(**kwargs)()
